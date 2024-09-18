import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

localdata = {}


def get_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)


def testcase(driver, test, label=''):
    try:
        print(f'\n⚙️ Start {label} test')
        test(driver)
        print(f'✅ {label} test passed')
    except Exception as e:
        print(f'❌ {label} test failed.')
        print(e)


def test_success_auth(browser: webdriver.Chrome):
    url = "https://saucedemo.com/"
    browser.get(url)

    username = browser.find_element(By.CSS_SELECTOR, "#user-name")
    password = browser.find_element(By.CSS_SELECTOR, "#password")
    login_button = browser.find_element(By.CSS_SELECTOR, '#login-button')

    # Ввод логина
    username.click()
    username.send_keys('standard_user')

    # Ввод пароля
    password.click()
    password.send_keys('secret_sauce')

    # Нажатие на кнопку "Login"
    login_button.click()

    correct_url = 'https://www.saucedemo.com/inventory.html'
    error_message = 'Адрес после нажатия на кнопку и тестовый не совпадают'
    assert browser.current_url == correct_url, error_message


def test_add_to_cart(browser: webdriver.Chrome):
    url = 'https://www.saucedemo.com/inventory.html'
    browser.get(url)

    # Получение случайного элемента списка товаров
    items = WebDriverWait(browser, 3).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.inventory_item'))
    )
    random_index = random.randint(0, len(items) - 1)
    item = items[random_index]

    # Переход на страницу товара. Это сделано для того, чтобы сохранить урл товара. В полном урле есть его id,
    # который используется для проверки товара в корзине
    label = item.find_element(By.CSS_SELECTOR, '.inventory_item_label').find_element(By.CSS_SELECTOR, 'a')
    label.click()
    product_url = browser.current_url
    time.sleep(10)
    browser.back()

    localdata['item_to_cart'] = {
        'url': product_url
    }

    items = browser.find_elements(By.CSS_SELECTOR, '.inventory_item')
    item = items[random_index]
    add_to_cart_button = item.find_element(By.CSS_SELECTOR, '.btn_inventory')
    remove_id = add_to_cart_button.get_attribute('id').replace('add-to-cart', 'remove')

    add_to_cart_button.click()

    # Получение баджа у иконки корзины
    cart_badge = WebDriverWait(browser, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.shopping_cart_badge'))
    )

    # Проверка на количество нажатых кнопок и значения баджа
    assert int(cart_badge.text) == 1, 'Число в бадже не совпадает с кол-вом добавленных товаров'

    # Проверка того, что у кнопки текст изменился на "Remove"
    add_to_cart_button = browser.find_element(By.CSS_SELECTOR, f'#{remove_id}')
    assert add_to_cart_button.text == 'Remove', 'Текст нажатой кнопки не поменялся на "Remove"'


def test_order_flow(browser: webdriver.Chrome):
    print('[1/4] Cart')
    url = 'https://www.saucedemo.com/cart.html'
    browser.get(url)

    # Сам товар
    label = browser.find_element(By.CSS_SELECTOR, '.cart_item_label')
    link = label.find_element(By.CSS_SELECTOR, 'a')

    # Переход по ссылке на товар, чтобы получить его адрес и сравнить id
    link.click()
    url = browser.current_url
    browser.back()

    assert url == localdata['item_to_cart']['url'], 'Адрес добавленного товара не соответствует адресу товара в корзине'

    # Кнопка перехода к оформлению
    checkout_button = browser.find_element(By.CSS_SELECTOR, '.checkout_button')
    checkout_button.click()

    print('[2/4] Checkout step one')
    # Поля для ввода
    first_name_input = browser.find_element(By.CSS_SELECTOR, '#first-name')
    last_name_input = browser.find_element(By.CSS_SELECTOR, '#last-name')
    postal_code_input = browser.find_element(By.CSS_SELECTOR, '#postal-code')
    continue_button = browser.find_element(By.CSS_SELECTOR, '#continue')

    first_name_input.send_keys('Firstname')
    last_name_input.send_keys('Lastnamov')
    postal_code_input.send_keys('800555')

    continue_button.click()

    print('[3/4] Checkout step two')

    continue_button = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '#finish'))
    )

    continue_button.click()

    print('[4/4] Checkout final')

    complete_header = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.complete-header'))
    ).text

    assert complete_header == 'Thank you for your order!', 'Заголовок успешного завершения заказа не совпадает с заданным'

    complete_text = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.complete-text'))
    ).text

    correct_complete_text = 'Your order has been dispatched, and will arrive just as fast as the pony can get there!'
    error_message = 'Текст успешного завершения заказа не совпадает с заданным'

    assert complete_text == correct_complete_text, error_message


driver = get_driver()
testcase(driver, test_success_auth, 'login')
testcase(driver, test_add_to_cart, 'add to cart')
testcase(driver, test_order_flow, 'order flow')

driver.quit()