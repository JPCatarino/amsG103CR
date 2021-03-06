package com.example.tests;

import java.util.regex.Pattern;
import java.util.concurrent.TimeUnit;
import org.junit.*;
import static org.junit.Assert.*;
import static org.hamcrest.CoreMatchers.*;
import org.openqa.selenium.*;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.Select;

public class CreateEvent1 {
  private WebDriver driver;
  private String baseUrl;
  private boolean acceptNextAlert = true;
  private StringBuffer verificationErrors = new StringBuffer();

  @Before
  public void setUp() throws Exception {
    driver = new FirefoxDriver();
    baseUrl = "https://www.katalon.com/";
    driver.manage().timeouts().implicitlyWait(30, TimeUnit.SECONDS);
  }

  @Test
  public void testCreateEvent1() throws Exception {
    driver.get("http://127.0.0.1:8080/");
    driver.findElement(By.linkText("Login")).click();
    driver.findElement(By.id("id_username")).clear();
    driver.findElement(By.id("id_username")).sendKeys("seltest");
    driver.findElement(By.id("id_password")).clear();
    driver.findElement(By.id("id_password")).sendKeys("seltest");
    driver.findElement(By.xpath("(.//*[normalize-space(text()) and normalize-space(.)='Password'])[1]/following::input[2]")).click();
    driver.findElement(By.linkText("Eventos")).click();
    driver.findElement(By.linkText("Criar Evento")).click();
    driver.findElement(By.id("id_nome")).click();
    driver.findElement(By.id("id_nome")).clear();
    driver.findElement(By.id("id_nome")).sendKeys("nEvent" + (Math.random() * ((2147483640 - 0) + 1)) + 0);
    driver.findElement(By.id("id_local")).clear();
    driver.findElement(By.id("id_local")).sendKeys("Porto");
    driver.findElement(By.id("id_data")).click();
    driver.findElement(By.id("id_data")).clear();
    driver.findElement(By.id("id_data")).sendKeys("21-05-2019");
    driver.findElement(By.id("id_hora")).clear();
    driver.findElement(By.id("id_hora")).sendKeys("19:00");
    driver.findElement(By.id("id_nmax")).clear();
    driver.findElement(By.id("id_nmax")).sendKeys("10000");
    driver.findElement(By.id("id_insc")).clear();
    driver.findElement(By.id("id_insc")).sendKeys("15");
    driver.findElement(By.xpath("(.//*[normalize-space(text()) and normalize-space(.)='Valor Inscrição'])[1]/following::input[2]")).click();
  }

  @After
  public void tearDown() throws Exception {
    driver.quit();
    String verificationErrorString = verificationErrors.toString();
    if (!"".equals(verificationErrorString)) {
      fail(verificationErrorString);
    }
  }

  private boolean isElementPresent(By by) {
    try {
      driver.findElement(by);
      return true;
    } catch (NoSuchElementException e) {
      return false;
    }
  }

  private boolean isAlertPresent() {
    try {
      driver.switchTo().alert();
      return true;
    } catch (NoAlertPresentException e) {
      return false;
    }
  }

  private String closeAlertAndGetItsText() {
    try {
      Alert alert = driver.switchTo().alert();
      String alertText = alert.getText();
      if (acceptNextAlert) {
        alert.accept();
      } else {
        alert.dismiss();
      }
      return alertText;
    } finally {
      acceptNextAlert = true;
    }
  }
}
