from ssl import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, WebDriverException)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from datetime import datetime
import time
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from contextlib import contextmanager
import statistics

# Configuración de timeouts adaptativos
ADAPTIVE_TIMEOUT_CONFIG = {
    'initial_page_load': 10,
    'min_page_load': 3,
    'max_page_load': 20,
    'initial_element_wait': 8,
    'min_element_wait': 2,
    'max_element_wait': 15,
    'login_timeout': 5,
    'implicit_wait': 2
}

# Historial de performance por sitio
SITE_PERFORMANCE_HISTORY = {}

# Configuración de paralelización
MAX_WORKERS = 5  # Número de hilos concurrentes optimizado

# Configuración de credenciales - usar variables de entorno en producción
CREDENCIALES = {
    'DEMO_PORTAL': {
        'username': os.getenv('DEMO_USERNAME', 'demo_user'),
        'password': os.getenv('DEMO_PASSWORD', 'demo_password')
    }
}

# Configuración de sitios web - Ejemplos de casos con y sin login
ALL_SITES = [
    # Ejemplo de sitio CON autenticación
    {
        'name': 'Demo Portal with Login',
        'requires_login': True,
        'credenciales_key': 'DEMO_PORTAL',
        'initial_url': 'https://example-portal.com/login',
        'username_xpath': '//*[@id="username"]',
        'password_xpath': '//*[@id="password"]',
        'login_button_xpath': '//*[@id="login-button"]',
        'success_url': 'https://example-portal.com/dashboard',
        'success_validation': 'contains',
        'success_element': '//*[contains(text(), "Welcome") or contains(@class, "dashboard")]',
        'estimated_time': 5
    },
    # Ejemplo de sitio SIN autenticación
    {
        'name': 'Public Services Portal',
        'requires_login': False,
        'initial_url': 'https://public-services.example.com/home',
        'success_url': 'https://public-services.example.com/home',
        'validation_element': '//body',
        'estimated_time': 3
    },
    # Ejemplo de servicio web/API
    {
        'name': 'Web Service API',
        'requires_login': False,
        'initial_url': 'https://api.example.com/service?wsdl',
        'success_url': 'https://api.example.com/service?wsdl',
        'validation_element': '//body',
        'estimated_time': 3
    },
    # Ejemplo de aplicación interna
    {
        'name': 'Internal Management System',
        'requires_login': True,
        'credenciales_key': 'DEMO_PORTAL',
        'initial_url': 'https://internal.example.com/login',
        'username_xpath': '//*[@id="user"]',
        'password_xpath': '//*[@id="pass"]',
        'login_button_xpath': '//*[@id="submit"]',
        'success_url': 'https://internal.example.com/main',
        'estimated_time': 5
    },
    # Ejemplo de sistema de documentos
    {
        'name': 'Document Management System',
        'requires_login': True,
        'credenciales_key': 'DEMO_PORTAL',
        'initial_url': 'https://docs.example.com/login',
        'username_xpath': '//*[@id="email"]',
        'password_xpath': '//*[@id="password"]',
        'login_button_xpath': '//button[@type="submit"]',
        'success_url': 'https://docs.example.com/documents',
        'estimated_time': 5
    },
    # Ejemplo de servicio público
    {
        'name': 'Public Information Portal',
        'requires_login': False,
        'initial_url': 'https://info.example.com/public',
        'success_url': 'https://info.example.com/public',
        'validation_element': '//body',
        'estimated_time': 3
    }
]

class CircuitBreaker:
    def __init__(self, threshold=3, reset_timeout=300):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure = 0
        self.lock = threading.Lock()
    
    def should_try(self):
        with self.lock:
            if self.failures >= self.threshold:
                if time.time() - self.last_failure > self.reset_timeout:
                    self.failures = 0  # Reset after timeout
                    return True
                return False
            return True
    
    def record_failure(self):
        with self.lock:
            self.failures += 1
            self.last_failure = time.time()

# Circuit breakers por sitio
CIRCUIT_BREAKERS = {site['name']: CircuitBreaker() for site in ALL_SITES}

class TestResult:
    def __init__(self, name, success, error_msg=None, duration=0, screenshot_path=None):
        self.name = name
        self.success = success
        self.error_msg = error_msg
        self.duration = duration
        self.screenshot_path = screenshot_path
        self.timestamp = datetime.now()

# Thread-local storage para drivers
thread_local = threading.local()

def take_screenshot(driver, name):
    """Toma screenshot optimizada para ejecución paralela"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = f"screenshots_{timestamp}"
        
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir, exist_ok=True)
            
        thread_id = threading.current_thread().ident
        filename = f"{screenshot_dir}/{name.replace(' ', '_')}_{thread_id}.png"
        driver.save_screenshot(filename)
        return filename
    except Exception as e:
        print(f"⚠️ Error al tomar captura: {str(e)}")
        return None

@contextmanager
def get_driver():
    """Context manager optimizado para manejo de drivers por hilo"""
    if not hasattr(thread_local, 'driver'):
        thread_local.driver = initialize_driver()
    
    driver = thread_local.driver
    try:
        yield driver
    except Exception as e:
        # En caso de error grave, limpiamos el driver
        driver.quit()
        del thread_local.driver
        raise e

def initialize_driver():
    """Inicializa un driver Chrome optimizado para testing paralelo"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(ADAPTIVE_TIMEOUT_CONFIG['implicit_wait'])
        return driver
    except WebDriverException as e:
        raise Exception(f"Error al iniciar el driver: {str(e)}")

def get_adaptive_timeout(site_name, timeout_type='page_load'):
    """Calcula timeout basado en historial de performance"""
    history = SITE_PERFORMANCE_HISTORY.get(site_name, {}).get(timeout_type, [])
    
    if not history:
        if timeout_type == 'page_load':
            return ADAPTIVE_TIMEOUT_CONFIG['initial_page_load']
        else:
            return ADAPTIVE_TIMEOUT_CONFIG['initial_element_wait']
    
    avg = statistics.mean(history)
    std_dev = statistics.stdev(history) if len(history) > 1 else 0
    
    if timeout_type == 'page_load':
        min_timeout = ADAPTIVE_TIMEOUT_CONFIG['min_page_load']
        max_timeout = ADAPTIVE_TIMEOUT_CONFIG['max_page_load']
    else:
        min_timeout = ADAPTIVE_TIMEOUT_CONFIG['min_element_wait']
        max_timeout = ADAPTIVE_TIMEOUT_CONFIG['max_element_wait']
    
    # Calculamos timeout como promedio + 1.5 desviaciones estándar
    calculated_timeout = avg + (1.5 * std_dev)
    
    # Aseguramos que esté dentro de los límites
    return max(min_timeout, min(max_timeout, calculated_timeout))

def update_performance_history(site_name, duration, success):
    """Actualiza el historial de performance para timeouts adaptativos"""
    if site_name not in SITE_PERFORMANCE_HISTORY:
        SITE_PERFORMANCE_HISTORY[site_name] = {
            'page_load': [],
            'element_wait': []
        }
    
    if success:
        SITE_PERFORMANCE_HISTORY[site_name]['page_load'].append(duration)
        # Mantenemos un historial razonable (últimas 10 ejecuciones)
        if len(SITE_PERFORMANCE_HISTORY[site_name]['page_load']) > 10:
            SITE_PERFORMANCE_HISTORY[site_name]['page_load'].pop(0)

def validate_page_optimized(driver, config, timeout):
    """Validación con múltiples estrategias y timeout adaptativo"""
    validation_passed = False
    wait = WebDriverWait(driver, timeout)
    
    try:
        # Estrategia 1: Validación por URL
        if 'success_url' in config:
            if config.get('success_validation', 'exact') == 'contains':
                wait.until(lambda d: config['success_url'] in d.current_url)
            else:
                wait.until(lambda d: d.current_url == config['success_url'])
            validation_passed = True
        
        # Estrategia 2: Validación por elemento
        if 'success_element' in config and not validation_passed:
            wait.until(EC.presence_of_element_located((By.XPATH, config['success_element'])))
            validation_passed = True
        
        # Estrategia 3: Validación por elemento genérico
        if 'validation_element' in config and not validation_passed:
            wait.until(EC.presence_of_element_located((By.XPATH, config['validation_element'])))
            validation_passed = True
        
        return validation_passed
        
    except TimeoutException:
        return False

def perform_login(driver, config, timeout):
    """Login optimizado con timeouts adaptativos"""
    try:
        creds = CREDENCIALES[config['credenciales_key']]
        wait = WebDriverWait(driver, timeout)
        
        # Usar expected conditions más específicas
        username_element = wait.until(
            EC.element_to_be_clickable((By.XPATH, config['username_xpath'])))
        username_element.clear()
        username_element.send_keys(creds['username'])
        
        password_element = wait.until(
            EC.element_to_be_clickable((By.XPATH, config['password_xpath'])))
        password_element.clear()
        password_element.send_keys(creds['password'])
        
        login_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, config['login_button_xpath'])))
        login_button.click()
        
        # Esperar redirección con timeout adaptativo
        WebDriverWait(driver, timeout).until(
            lambda d: d.current_url != config['initial_url'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error en login para {config['name']}: {str(e)}")
        return False

def test_site_thread_safe(config):
    """Versión optimizada para ejecución paralela"""
    site_name = config['name']
    start_time = time.time()
    
    # Obtener timeouts adaptativos
    page_load_timeout = get_adaptive_timeout(site_name, 'page_load')
    element_wait_timeout = get_adaptive_timeout(site_name, 'element_wait')
    
    with get_driver() as driver:
        try:
            driver.set_page_load_timeout(page_load_timeout)
            print(f"🔍 [{threading.current_thread().name}] Probando: {site_name} (Timeout: {page_load_timeout}s)")
            
            # 1. Cargar página inicial
            driver.get(config['initial_url'])
            
            # 2. Validar carga básica de página
            WebDriverWait(driver, element_wait_timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete")
            
            screenshot_path = take_screenshot(driver, f"{site_name}_inicio")
            
            # 3. Proceso de login si es requerido
            if config.get('requires_login', False):
                login_success = perform_login(driver, config, element_wait_timeout)
                if not login_success:
                    duration = time.time() - start_time
                    update_performance_history(site_name, duration, False)
                    return TestResult(site_name, False, "Login failed", duration, screenshot_path)

            # 4. Validación de página
            validation_result = validate_page_optimized(driver, config, element_wait_timeout)
            duration = time.time() - start_time
            
            if validation_result:
                success_screenshot = take_screenshot(driver, f"{site_name}_exitoso")
                update_performance_history(site_name, duration, True)
                print(f"✅ [{threading.current_thread().name}] Prueba exitosa: {site_name} ({duration:.2f}s)")
                return TestResult(site_name, True, None, duration, success_screenshot)
            else:
                fail_screenshot = take_screenshot(driver, f"{site_name}_fallido")
                update_performance_history(site_name, duration, False)
                return TestResult(site_name, False, "Validation failed", duration, fail_screenshot)
                
        except TimeoutException as e:
            duration = time.time() - start_time
            error_screenshot = take_screenshot(driver, f"{site_name}_timeout")
            update_performance_history(site_name, duration, False)
            return TestResult(site_name, False, f"Timeout after {duration:.2f}s", duration, error_screenshot)
            
        except Exception as e:
            duration = time.time() - start_time
            error_screenshot = take_screenshot(driver, f"{site_name}_error")
            update_performance_history(site_name, duration, False)
            return TestResult(site_name, False, str(e), duration, error_screenshot)

def test_site_with_retries(config, max_retries=2):
    """Ejecuta prueba con reintentos y circuit breaker"""
    site_name = config['name']
    circuit_breaker = CIRCUIT_BREAKERS[site_name]
    
    if not circuit_breaker.should_try():
        return TestResult(site_name, False, "Circuit breaker activado (servicio no disponible)")
    
    for attempt in range(max_retries + 1):
        try:
            result = test_site_thread_safe(config)
            
            if result.success:
                circuit_breaker.failures = 0  # Reset circuit breaker on success
                return result
            else:
                circuit_breaker.record_failure()
                
            if attempt == max_retries:
                return result
                
            print(f"🔄 Reintentando {site_name} (intento {attempt + 2}/{max_retries + 1})")
            time.sleep(1)  # Pequeño delay entre reintentos
            
        except Exception as e:
            circuit_breaker.record_failure()
            if attempt == max_retries:
                return TestResult(site_name, False, f"Error después de {max_retries} reintentos: {str(e)}")

def generate_enhanced_pdf_report(results, filename=None):
    """Genera reporte PDF con métricas mejoradas"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_pruebas_{timestamp}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#003366")
    )
    
    success_style = ParagraphStyle(
        'Success',
        parent=styles['Normal'],
        textColor=colors.green,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    fail_style = ParagraphStyle(
        'Fail',
        parent=styles['Normal'],
        textColor=colors.red,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # Título y fecha
    story.append(Paragraph("Reporte de Testing Automatizado - Web Applications", title_style))
    story.append(Paragraph(f"<b>Fecha de ejecución:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Estadísticas generales
    total = len(results)
    passed = sum(1 for r in results if r.success)
    failed = total - passed
    avg_duration = sum(r.duration for r in results) / total if results else 0
    total_duration = sum(r.duration for r in results)
    
    story.append(Paragraph("<b>RESUMEN EJECUTIVO</b>", styles['Heading2']))
    story.append(Paragraph(f"<b>Total de pruebas:</b> {total}", styles['Normal']))
    story.append(Paragraph(f"<b>Pruebas exitosas:</b> <font color='green'>{passed} ({passed/total*100:.1f}%)</font>", styles['Normal']))
    story.append(Paragraph(f"<b>Pruebas fallidas:</b> <font color='red'>{failed} ({failed/total*100:.1f}%)</font>", styles['Normal']))
    story.append(Paragraph(f"<b>Tiempo total de ejecución:</b> {total_duration:.2f} segundos", styles['Normal']))
    story.append(Paragraph(f"<b>Tiempo promedio por prueba:</b> {avg_duration:.2f} segundos", styles['Normal']))
    
    # Historial de performance
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>HISTORIAL DE PERFORMANCE</b>", styles['Heading2']))
    for site, history in SITE_PERFORMANCE_HISTORY.items():
        if history['page_load']:
            avg_time = statistics.mean(history['page_load'])
            story.append(Paragraph(f"• {site}: {avg_time:.2f}s (últimas {len(history['page_load'])} ejecuciones)", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Detalle por categorías
    story.append(Paragraph("<b>RESULTADOS DETALLADOS</b>", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    # Pruebas exitosas
    story.append(Paragraph("<b>Pruebas Exitosas:</b>", styles['Heading3']))
    for result in [r for r in results if r.success]:
        story.append(Paragraph(f"✓ {result.name} ({result.duration:.2f}s)", success_style))
    
    story.append(Spacer(1, 10))
    
    # Pruebas fallidas
    story.append(Paragraph("<b>Pruebas Fallidas:</b>", styles['Heading3']))
    for result in [r for r in results if not r.success]:
        error_msg = f" - {result.error_msg}" if result.error_msg else ""
        story.append(Paragraph(f"✗ {result.name} ({result.duration:.2f}s){error_msg}", fail_style))
    
    doc.build(story)
    print(f"\n📄 Reporte PDF generado: {filename}")
    return filename

def balance_test_groups(sites, workers):
    """Balancea las pruebas por tiempo estimado"""
    sorted_sites = sorted(sites, key=lambda x: x.get('estimated_time', 5), reverse=True)
    groups = [[] for _ in range(workers)]
    
    for i, site in enumerate(sorted_sites):
        groups[i % workers].append(site)
    
    return groups

def cleanup_resources():
    """Limpia todos los recursos (drivers) al finalizar"""
    print("🧹 Limpiando recursos...")
    if hasattr(thread_local, 'driver'):
        try:
            thread_local.driver.quit()
            del thread_local.driver
        except:
            pass

def run_parallel_tests(sites, max_workers=MAX_WORKERS):
    """Ejecuta pruebas en paralelo con balanceo de carga"""
    results = []
    total_start_time = time.time()
    
    print(f"🚀 Iniciando pruebas paralelas con {max_workers} workers...")
    print(f"📊 Total de sitios a probar: {len(sites)}")
    print(f"⏱️ Timeouts adaptativos activados")
    print("=" * 60)
    
    # Balancear pruebas por tiempo estimado
    test_groups = balance_test_groups(sites, max_workers)
    
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="TestWorker") as executor:
        # Enviar todas las tareas balanceadas
        future_to_site = {}
        for group in test_groups:
            for site in group:
                future = executor.submit(test_site_with_retries, site)
                future_to_site[future] = site['name']
        
        # Recoger resultados
        for future in as_completed(future_to_site):
            site_name = future_to_site[future]
            try:
                result = future.result()
                results.append(result)
                
                # Mostrar progreso
                completed = len(results)
                progress = (completed / len(sites)) * 100
                print(f"📈 Progreso: {completed}/{len(sites)} ({progress:.1f}%) - Último: {site_name}")
                
            except Exception as e:
                error_result = TestResult(site_name, False, f"Exception: {str(e)}")
                results.append(error_result)
                print(f"❌ Error inesperado en {site_name}: {str(e)}")
    
    total_duration = time.time() - total_start_time
    
    print("=" * 60)
    print(f"⏱️  Ejecución completada en {total_duration:.2f} segundos")
    print(f"⚡ Tiempo promedio por prueba: {total_duration/len(sites):.2f}s")
    estimated_sequential = sum(s.get('estimated_time', 5) for s in sites)
    print(f"🚀 Mejora estimada vs secuencial: {(estimated_sequential - total_duration):.2f}s")
    
    return results, total_duration

def main():
    """Función principal optimizada"""
    print("🚀 Web Testing Tool Optimizado - Versión 2.0")
    print(f"⚙️  Configuración: {MAX_WORKERS} workers paralelos")
    print(f"🔄 Timeouts adaptativos activados")
    
    try:
        # Ejecutar pruebas en paralelo
        results, total_duration = run_parallel_tests(ALL_SITES, MAX_WORKERS)
        
        # Mostrar resumen final
        print("\n" + "=" * 60)
        print("📊 REPORTE FINAL DE EJECUCIÓN")
        print("=" * 60)
        
        passed = sum(1 for r in results if r.success)
        failed = len(results) - passed
        
        print(f"✅ Pruebas exitosas: {passed} ({passed/len(results)*100:.1f}%)")
        print(f"❌ Pruebas fallidas: {failed} ({failed/len(results)*100:.1f}%)")
        print(f"⏱️  Tiempo total: {total_duration:.2f} segundos")
        print(f"📈 Performance media: {total_duration/len(results):.2f}s por prueba")
        
        # Generar reporte PDF
        pdf_filename = generate_enhanced_pdf_report(results)
        print(f"\n📄 Reporte generado: {pdf_filename}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n⚠️ Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {str(e)}")
        raise
    finally:
        cleanup_resources()

if __name__ == "__main__":
    main()