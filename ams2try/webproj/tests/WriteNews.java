package com.example.tests;

import java.util.regex.Pattern;
import java.util.concurrent.TimeUnit;
import org.junit.*;
import static org.junit.Assert.*;
import static org.hamcrest.CoreMatchers.*;
import org.openqa.selenium.*;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.Select;

public class WriteNews {
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
  public void testWriteNews() throws Exception {
    driver.get("http://127.0.0.1:8080/");
    driver.findElement(By.linkText("Login")).click();
    driver.findElement(By.id("id_username")).clear();
    driver.findElement(By.id("id_username")).sendKeys("seltest");
    driver.findElement(By.id("id_password")).clear();
    driver.findElement(By.id("id_password")).sendKeys("seltest");
    driver.findElement(By.id("id_password")).sendKeys(Keys.ENTER);
    driver.findElement(By.linkText("Noticias")).click();
    driver.findElement(By.linkText("Escrever Noticia")).click();
    driver.findElement(By.id("id_new")).click();
    driver.findElement(By.id("id_new")).clear();
    driver.findElement(By.id("id_new")).sendKeys("teste de selenium!");
    driver.findElement(By.xpath("(.//*[normalize-space(text()) and normalize-space(.)='Organizador'])[1]/following::input[2]")).click();
    driver.findElement(By.linkText("Publicadas")).click();
    assertEquals("teste de selenium!", driver.findElement(By.xpath("(.//*[normalize-space(text()) and normalize-space(.)='seltest'])[8]/following::td[1]")).getText());
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
