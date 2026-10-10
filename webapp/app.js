/**
 * Telegram Mini App Kalkulyator Dasturi (JavaScript)
 * Telegram WebApp SDK integratsiyasi, ilmiy hisob-kitoblar,
 * haptik tebranish va real vaqtdagi hisoblash.
 */

(function () {
  'use strict';

  // 1. Telegram WebApp obyektini sozlash
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    tg.expand();
    // Telegram mavzusiga moslashish
    if (tg.colorScheme === 'dark') {
      document.body.classList.add('dark-theme');
    }
  }

  // Haptik tebranish funksiyasi (Telefon tebranishi)
  function triggerHaptic(type = 'light') {
    try {
      if (tg?.HapticFeedback) {
        if (type === 'success' || type === 'error' || type === 'warning') {
          tg.HapticFeedback.notificationOccurred(type);
        } else {
          tg.HapticFeedback.impactOccurred(type);
        }
      }
    } catch (e) {
      // Brauzerda xatolik bermasligi uchun
    }
  }

  // 2. Foydalanuvchi ma'lumotlarini o'rnatish
  const userNameEl = document.getElementById('userName');
  const userGreetingEl = document.getElementById('userGreeting');
  const userAvatarEl = document.getElementById('userAvatar');

  if (tg?.initDataUnsafe?.user) {
    const user = tg.initDataUnsafe.user;
    const name = user.first_name || 'Foydalanuvchi';
    userNameEl.textContent = name;
    userGreetingEl.textContent = 'Salom!';
    if (name.length > 0) {
      userAvatarEl.textContent = name[0].toUpperCase();
    }
  }

  // 3. Holat o'zgaruvchilari (State)
  let currentExpr = '';
  let lastResult = '0';
  let isEvaluated = false;
  let angleMode = 'DEG'; // 'DEG' yoki 'RAD'
  let history = [];

  // LocalStorage dan tarixni yuklash
  try {
    const saved = localStorage.getItem('calc_history');
    if (saved) {
      history = JSON.parse(saved);
    }
  } catch (e) {
    history = [];
  }

  // 4. Elementlar
  const expressionLine = document.getElementById('expressionLine');
  const resultValue = document.getElementById('resultValue');
  const equalSign = document.getElementById('equalSign');
  const angleToggle = document.getElementById('angleToggle');
  const toastMessage = document.getElementById('toastMessage');

  const tabStandard = document.getElementById('tabStandard');
  const tabScientific = document.getElementById('tabScientific');
  const tabHistory = document.getElementById('tabHistory');

  const standardKeypad = document.getElementById('standardKeypad');
  const scientificKeypad = document.getElementById('scientificKeypad');
  const historyView = document.getElementById('historyView');
  const historyList = document.getElementById('historyList');
  const historyEmpty = document.getElementById('historyEmpty');

  // 5. Toast xabarnomasini ko'rsatish
  function showToast(msg) {
    toastMessage.textContent = msg;
    toastMessage.classList.add('show');
    setTimeout(() => {
      toastMessage.classList.remove('show');
    }, 2200);
  }

  // 6. DEG / RAD rejimini almashtirish
  angleToggle.addEventListener('click', () => {
    triggerHaptic('selection');
    angleMode = angleMode === 'DEG' ? 'RAD' : 'DEG';
    angleToggle.textContent = angleMode;
    updateDisplay();
  });

  // 7. Tablarni boshqarish
  const tabs = [
    { btn: tabStandard, view: standardKeypad },
    { btn: tabScientific, view: scientificKeypad },
    { btn: tabHistory, view: historyView, onOpen: renderHistory },
  ];

  tabs.forEach((tab) => {
    tab.btn.addEventListener('click', () => {
      triggerHaptic('light');
      tabs.forEach((t) => {
        t.btn.classList.remove('active');
        t.view.classList.remove('active');
      });
      tab.btn.classList.add('active');
      tab.view.classList.add('active');
      if (tab.onOpen) tab.onOpen();
    });
  });

  // 8. Ekranni yangilash va shrift o'lchamini moslash
  function updateDisplay(previewVal = null) {
    expressionLine.textContent = currentExpr || '0';

    const valToShow = previewVal !== null ? previewVal : lastResult;
    resultValue.textContent = formatDisplayNumber(valToShow);

    // Katta sonlar uchun shriftni kichraytirish
    const len = resultValue.textContent.length;
    if (len > 14) {
      resultValue.style.fontSize = '22px';
    } else if (len > 9) {
      resultValue.style.fontSize = '28px';
    } else {
      resultValue.style.fontSize = '36px';
    }

    expressionLine.scrollLeft = expressionLine.scrollWidth;
  }

  function formatDisplayNumber(numStr) {
    if (!numStr || isNaN(Number(numStr))) return numStr;
    const num = Number(numStr);
    if (Math.abs(num) >= 1e12 || (Math.abs(num) < 1e-6 && num !== 0)) {
      return num.toExponential(4);
    }
    // Butun son bo'lsa
    if (Number.isInteger(num)) {
      return num.toLocaleString('uz-UZ');
    }
    return String(Math.round(num * 1e8) / 1e8);
  }

  // 9. Matematik tahlilchi va hisoblagich (JS Engine)
  function evaluateMath(raw) {
    if (!raw || !raw.trim()) return null;

    let expr = raw.trim();

    // Belgilarni almashtirish
    expr = expr.replace(/×/g, '*').replace(/÷/g, '/').replace(/−/g, '-');
    expr = expr.replace(/\^/g, '**');

    // Bo'shliqlarni tozalash (raqamlar orasidagi)
    expr = expr.replace(/(\d)\s+(\d)/g, '$1$2');

    // Foizlarni qayta ishlash:
    // A + B% -> A + (A * B / 100)
    expr = expr.replace(/([0-9.]+)\s*([\+\-])\s*([0-9.]+)\s*%(?!\s*\d)/g, '$1 $2 ($1 * $3 / 100)');
    expr = expr.replace(/([\*\/])\s*([0-9.]+)\s*%(?!\s*\d)/g, '$1 ($2 / 100)');
    expr = expr.replace(/([0-9.]+)\s*%(?!\s*\d)/g, '($1 / 100)');

    // Ildiz: √(x) yoki √x
    expr = expr.replace(/√\(([^)]+)\)/g, 'Math.sqrt($1)');
    expr = expr.replace(/√([0-9.]+)/g, 'Math.sqrt($1)');

    // Faktorial: n! -> factorial(n)
    expr = expr.replace(/([0-9.]+)!/g, 'calcFactorial($1)');

    // Yashirin ko'paytirish: 2(3+4) -> 2*(3+4), 2pi -> 2*Math.PI
    expr = expr.replace(/(\d)\s*\(/g, '$1 * (');
    expr = expr.replace(/\)\s*(\d)/g, ') * $1');
    expr = expr.replace(/\)\s*\(/g, ') * (');
    expr = expr.replace(/(\d)\s*(Math|pi|e|sin|cos|tan|log|abs)\b/g, '$1 * $2');

    // Matematik funksiyalar va doimiylar
    const isDeg = angleMode === 'DEG';
    const scope = {
      Math: Math,
      pi: Math.PI,
      e: Math.E,
      abs: Math.abs,
      sqrt: Math.sqrt,
      log: Math.log,       // natural ln
      log10: Math.log10,   // log10
      sin: (x) => Math.sin(isDeg ? (x * Math.PI) / 180 : x),
      cos: (x) => Math.cos(isDeg ? (x * Math.PI) / 180 : x),
      tan: (x) => Math.tan(isDeg ? (x * Math.PI) / 180 : x),
      calcFactorial: (n) => {
        n = Math.round(Number(n));
        if (n < 0 || n > 100) throw new Error('Faktorial xato');
        let r = 1;
        for (let i = 2; i <= n; i++) r *= i;
        return r;
      },
    };

    try {
      // Xavfsiz Function chaqiruvi (faqat berilgan matematik doirada)
      const keys = Object.keys(scope);
      const values = Object.values(scope);
      const fn = new Function(...keys, `"use strict"; return (${expr});`);
      const res = fn(...values);

      if (typeof res !== 'number' || isNaN(res) || !isFinite(res)) {
        return null;
      }
      return res;
    } catch (e) {
      return null;
    }
  }

  // 10. Jonli oldindan ko'rish (Live preview)
  function triggerLivePreview() {
    if (!currentExpr) {
      lastResult = '0';
      updateDisplay();
      return;
    }
    const val = evaluateMath(currentExpr);
    if (val !== null) {
      updateDisplay(String(val));
    } else {
      updateDisplay();
    }
  }

  // 11. Tugmalarni bosish mantig'i
  function handleInput(token) {
    triggerHaptic('light');

    if (isEvaluated) {
      // Agar avval natija olingan bo'lsa va operator bosilsa, natijani davom ettiramiz
      if (['+', '−', '×', '÷', '^', '%'].includes(token)) {
        currentExpr = lastResult + ' ' + token + ' ';
      } else {
        currentExpr = '';
      }
      isEvaluated = false;
    }

    currentExpr += token;
    triggerLivePreview();
  }

  function handleOperator(op) {
    triggerHaptic('medium');

    if (isEvaluated) {
      currentExpr = lastResult;
      isEvaluated = false;
    }

    if (!currentExpr) {
      currentExpr = '0';
    }

    currentExpr = currentExpr.trim() + ' ' + op + ' ';
    updateDisplay();
  }

  function handleClear() {
    triggerHaptic('warning');
    currentExpr = '';
    lastResult = '0';
    isEvaluated = false;
    updateDisplay();
  }

  function handleBackspace() {
    triggerHaptic('light');
    if (isEvaluated) {
      handleClear();
      return;
    }
    currentExpr = currentExpr.trimEnd();
    if (currentExpr.length > 0) {
      // Agar oxirgi belgi operator bo'lsa (masalan " + ")
      if (currentExpr.endsWith(' +') || currentExpr.endsWith(' −') || currentExpr.endsWith(' ×') || currentExpr.endsWith(' ÷')) {
        currentExpr = currentExpr.slice(0, -2).trimEnd();
      } else {
        currentExpr = currentExpr.slice(0, -1).trimEnd();
      }
    }
    triggerLivePreview();
  }

  function handleEqual() {
    if (!currentExpr.trim()) return;

    const res = evaluateMath(currentExpr);
    if (res !== null) {
      triggerHaptic('success');
      const formatted = String(Math.round(res * 1e8) / 1e8);
      addToHistory(currentExpr, formatted);
      lastResult = formatted;
      isEvaluated = true;
      updateDisplay(formatted);
    } else {
      triggerHaptic('error');
      showToast('⚠️ Ifodada xatolik bor!');
    }
  }

  // 12. Tarixga qo'shish
  function addToHistory(expr, res) {
    const time = new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit' });
    history.unshift({ expr, result: res, time });
    if (history.length > 20) history = history.slice(0, 20);
    try {
      localStorage.setItem('calc_history', JSON.stringify(history));
    } catch (e) {}
  }

  function renderHistory() {
    historyList.innerHTML = '';
    if (history.length === 0) {
      historyEmpty.style.display = 'flex';
      historyList.appendChild(historyEmpty);
      return;
    }

    historyEmpty.style.display = 'none';
    history.forEach((item, index) => {
      const card = document.createElement('div');
      card.className = 'history-item';
      card.innerHTML = `
        <div class="history-item-top">
          <span>${item.expr}</span>
          <span>${item.time}</span>
        </div>
        <div class="history-item-res">= ${item.result}</div>
      `;
      card.addEventListener('click', () => {
        triggerHaptic('medium');
        currentExpr = item.result;
        lastResult = item.result;
        isEvaluated = true;
        // Standart tabga qaytish
        tabStandard.click();
        updateDisplay();
        showToast('Natija kalkulyatorga yuklandi');
      });
      historyList.appendChild(card);
    });
  }

  document.getElementById('btnClearHistory').addEventListener('click', () => {
    triggerHaptic('warning');
    history = [];
    try {
      localStorage.removeItem('calc_history');
    } catch (e) {}
    renderHistory();
    showToast('Tarix tozalandi');
  });

  // 13. "Chatga yuborish" tugmasi (Telegram WebApp orqali botga ma'lumot yuborish)
  function sendResultToBot() {
    triggerHaptic('success');

    // Agar hisoblanmagan bo'lsa, hisoblaymiz
    if (!isEvaluated && currentExpr.trim()) {
      handleEqual();
    }

    const payload = {
      action: 'calculator_result',
      expression: currentExpr || lastResult,
      result: lastResult,
      timestamp: new Date().toISOString(),
    };

    if (tg && typeof tg.sendData === 'function') {
      // Telegram WebApp orqali to'g'ridan-to'g'ri botga yuborish
      tg.sendData(JSON.stringify(payload));
    } else {
      // Agar oddiy brauzerda test qilinayotgan bo'lsa
      navigator.clipboard?.writeText(`${payload.expression} = ${payload.result}`);
      showToast(`Natija (${payload.result}) nusxalandi!`);
    }
  }

  // 14. Event Listenerlarni biriktirish
  document.querySelectorAll('[data-insert]').forEach((btn) => {
    btn.addEventListener('click', () => handleInput(btn.getAttribute('data-insert')));
  });

  document.querySelectorAll('[data-op]').forEach((btn) => {
    btn.addEventListener('click', () => handleOperator(btn.getAttribute('data-op')));
  });

  document.getElementById('btnClear').addEventListener('click', handleClear);
  document.getElementById('btnSciClear').addEventListener('click', handleClear);

  document.getElementById('btnBackspace').addEventListener('click', handleBackspace);
  document.getElementById('btnSciBackspace').addEventListener('click', handleBackspace);

  document.getElementById('btnEqual').addEventListener('click', handleEqual);
  document.getElementById('btnSciEqual').addEventListener('click', handleEqual);

  document.getElementById('btnSendToChat').addEventListener('click', sendResultToBot);
  document.getElementById('btnSciSendToChat').addEventListener('click', sendResultToBot);

  // Klaviaturadan kiritishni qo'llab-quvvatlash (Desktop uchun)
  window.addEventListener('keydown', (e) => {
    if ((e.key >= '0' && e.key <= '9') || e.key === '.') {
      handleInput(e.key);
    } else if (['+', '-', '*', '/'].includes(e.key)) {
      const map = { '+': '+', '-': '−', '*': '×', '/': '÷' };
      handleOperator(map[e.key]);
    } else if (e.key === 'Enter' || e.key === '=') {
      e.preventDefault();
      handleEqual();
    } else if (e.key === 'Backspace') {
      handleBackspace();
    } else if (e.key === 'Escape') {
      handleClear();
    }
  });

  // Dastlabki holat
  updateDisplay();
})();
