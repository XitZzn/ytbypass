(function() {
  'use strict';

  const DEFAULT_IMGS = [
    'https://media.gettyimages.com/id/2226947078/pt/foto/former-brazilian-president-jair-bolsonaro-waves-to-supporters-during-a-meeting-with.jpg?s=612x612&w=0&k=20&c=7w8Be_nbjVUP_8cxB1oSTkLQnGg8-SMpHJHfdkNxWVo=',
    'https://media.gettyimages.com/id/2224823269/pt/foto/former-brazilian-president-jair-bolsonaro-speaks-to-the-press-at-the-federal-senate-in.jpg?s=612x612&w=0&k=20&c=V8ZmLDQtSWiDpg6CXDKfARyB_lUlSrLgc3HrNYxIOe8=',
    'https://media.gettyimages.com/id/2208290702/pt/foto/michelle-bolsonaro-speaks-next-to-her-husband-brazils-former-president-jair-bolsonaro-and.jpg?s=612x612&w=0&k=20&c=Wn-rBgNUmuHdvlOdpfWWZwfv6X97YLP9xfMBCqxIr6I=',
    'https://media.gettyimages.com/id/2221992973/pt/foto/brazils-former-president-jair-bolsonaro-attends-a-rally-on-paulista-avenue-in-sao-paulo-brazil.jpg?s=612x612&w=0&k=20&c=_1NGIavZWuAvuKMcV6GaF3oAX9EpwLc6ESrMQHqFQFY=',
    'https://media.gettyimages.com/id/2296924587/pt/foto/topshot-brazilian-right-wing-presidential-candidate-flavio-bolsonaro-holds-a-picture-of-his.jpg?s=612x612&w=0&k=20&c=XPRk5_boMsHp_PztBWdN4hyHcVztEbXb3wN2HZQNIsc=',
    'https://media.gettyimages.com/id/2229641416/pt/foto/former-brazilian-president-jair-bolsonaro-gestures-after-taking-medical-tests-at-df-star.jpg?s=612x612&w=0&k=20&c=KbkueX-vskL-yfpXqRsEFuO7-vtxKhhA9-ixKd0bjfE=',
    'https://media.gettyimages.com/id/1136844673/pt/foto/washington-dc-u-s-president-donald-trump-greets-brazilian-president-jair-bolsonaro-upon-his.jpg?s=612x612&w=0&k=20&c=EBdfm9x501AlX5bWkr1knctxYW6ZDgL1PAN24NmCWJg=',
    'https://media.gettyimages.com/id/2266861030/pt/foto/brazilian-senator-and-pre-presidential-candidate-flavio-bolsonaro-looks-on-as-he-speaks-with.jpg?s=612x612&w=0&k=20&c=JGjRW6ILwVuqXiW4UeGnR-1Jn63s2PxK45CvschgBX8=',
    'https://media.gettyimages.com/id/2225461039/pt/foto/jair-bolsonaro-brazils-former-president-departs-meetings-at-the-national-congress-in-brasilia.jpg?s=612x612&w=0&k=20&c=4evLuWOqFzHkJjOajpzNIBkgA1sj_BFhxFp_UpkRlYE=',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ad/Foto_oficial_do_senador_Fl%C3%A1vio_Bolsonaro_%28v._AgSen%29.jpg/960px-Foto_oficial_do_senador_Fl%C3%A1vio_Bolsonaro_%28v._AgSen%29.jpg',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/25/Entrevistas_-_Senador_Fl%C3%A1vio_Bolsonaro_%28Republicanos-RJ%29_e_advogado_Frederick_Wassef.jpg/960px-Entrevistas_-_Senador_Fl%C3%A1vio_Bolsonaro_%28Republicanos-RJ%29_e_advogado_Frederick_Wassef.jpg',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/79/Donald_Trump%2C_Eduardo_Bolsonaro%2C_Fl%C3%A1vio_Bolsonaro%2C_and_Paulo_Figueiredo.jpg/960px-Donald_Trump%2C_Eduardo_Bolsonaro%2C_Fl%C3%A1vio_Bolsonaro%2C_and_Paulo_Figueiredo.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/1/1f/Deputado_Estadual_Fl%C3%A1vio_Bolsonaro_em_formatura_do_grupamento_de_interven%C3%A7%C3%A3o_t%C3%A1tica.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/3/38/Deputado_Estadual_Fl%C3%A1vio_Bolsonaro_em_formatura_do_grupamento_de_interven%C3%A7%C3%A3o_t%C3%A1tica_%28cropped%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/5/5e/Fl%C3%A1vio_Bolsonaro.jpg',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e5/Pedro_Guimar%C3%A3es%2C_Jair_Bolsonaro_e_Fl%C3%A1vio_Bolsonaro.jpg/960px-Pedro_Guimar%C3%A3es%2C_Jair_Bolsonaro_e_Fl%C3%A1vio_Bolsonaro.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/0/00/2026_FLAVIO_BOLSONARO_CANDIDATO_PRESIDENTE_TSE_%28280002551544%29_%28cropped%29.jpg',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0a/Fl%C3%A1vio_Bolsonaro_em_entrevista_%283x4%29.jpg/960px-Fl%C3%A1vio_Bolsonaro_em_entrevista_%283x4%29.jpg'
  ];

  const REPLACED_ATTR = 'data-ncage-replaced';
  const storageArea = (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.sync) 
    ? chrome.storage.sync 
    : (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local ? chrome.storage.local : null);

  let currentConfig = {
    enabled: true,
    baseRate: 1,
    autoIncrease: true,
    startDate: null,
    images: DEFAULT_IMGS
  };

  function calculateEffectiveRate() {
    if (!currentConfig.enabled) return 0;
    let rate = currentConfig.baseRate;
    
    // Se o aumento diário de 1% estiver ativo
    if (currentConfig.autoIncrease && currentConfig.startDate) {
      const startMs = new Date(currentConfig.startDate).getTime();
      const nowMs = Date.now();
      const daysElapsed = Math.max(0, Math.floor((nowMs - startMs) / (1000 * 60 * 60 * 24)));
      rate = rate + (daysElapsed * 1);
    }
    
    return Math.min(100, Math.max(0, rate));
  }

  function updateConfig(items) {
    if (!items) return;
    if (typeof items.enabled !== 'undefined') currentConfig.enabled = items.enabled;
    if (typeof items.rate !== 'undefined') currentConfig.baseRate = parseInt(items.rate, 10) || 1;
    if (typeof items.autoIncrease !== 'undefined') currentConfig.autoIncrease = !!items.autoIncrease;
    if (items.startDate) currentConfig.startDate = items.startDate;
    
    if (items.library && typeof items.library === 'string') {
      const customUrls = items.library.split(',').map(u => u.trim()).filter(Boolean);
      currentConfig.images = customUrls.length > 0 ? customUrls : DEFAULT_IMGS;
    } else {
      currentConfig.images = DEFAULT_IMGS;
    }
  }

  // Carrega configuração salva
  if (storageArea) {
    storageArea.get({ enabled: true, rate: 1, autoIncrease: true, library: '', startDate: null }, function(items) {
      if (!items.startDate) {
        items.startDate = new Date().toISOString();
        storageArea.set({ startDate: items.startDate });
      }
      updateConfig(items);
      replaceAllImages();
    });

    if (chrome.storage.onChanged) {
      chrome.storage.onChanged.addListener(function(changes) {
        let changedItems = {};
        for (let key in changes) {
          changedItems[key] = changes[key].newValue;
        }
        updateConfig(changedItems);
        replaceAllImages();
      });
    }
  }

  function getRandomImage() {
    const list = currentConfig.images.length > 0 ? currentConfig.images : DEFAULT_IMGS;
    return list[Math.floor(Math.random() * list.length)];
  }

  function shouldReplace() {
    if (!currentConfig.enabled) return false;
    const effectiveRate = calculateEffectiveRate();
    if (effectiveRate >= 100) return true;
    if (effectiveRate <= 0) return false;
    return (Math.random() * 100) <= effectiveRate;
  }

  function isReplaced(img) {
    return img.getAttribute(REPLACED_ATTR) === 'true' || currentConfig.images.indexOf(img.src) !== -1;
  }

  function replaceImage(img) {
    if (isReplaced(img)) return;
    if (img.getAttribute(REPLACED_ATTR) === 'skipped') return;

    if (!shouldReplace()) {
      img.setAttribute(REPLACED_ATTR, 'skipped');
      return;
    }

    const w = img.clientWidth || img.naturalWidth || img.width || 100;
    const h = img.clientHeight || img.naturalHeight || img.height || 100;
    if (w > 25 && h > 25) {
      img.style.width = w + 'px';
      img.style.height = h + 'px';
      img.src = getRandomImage();
      img.setAttribute(REPLACED_ATTR, 'true');
    }
  }

  function replaceAllImages() {
    if (!currentConfig.enabled) return;
    const imgs = document.querySelectorAll('img');
    for (let i = 0; i < imgs.length; i++) {
      replaceImage(imgs[i]);
    }
  }

  // Executa no carregamento inicial
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', replaceAllImages);
  } else {
    replaceAllImages();
  }

  // Intervalo para sites dinâmicos (YouTube, redes sociais, etc.)
  setInterval(replaceAllImages, 2500);

  // Observador de mutações do DOM
  try {
    const observer = new MutationObserver(function(mutations) {
      if (!currentConfig.enabled) return;
      for (let i = 0; i < mutations.length; i++) {
        const nodes = mutations[i].addedNodes;
        for (let j = 0; j < nodes.length; j++) {
          const node = nodes[j];
          if (node.nodeType === 1) {
            if (node.tagName === 'IMG') {
              replaceImage(node);
            } else if (node.querySelectorAll) {
              const innerImgs = node.querySelectorAll('img');
              for (let k = 0; k < innerImgs.length; k++) {
                replaceImage(innerImgs[k]);
              }
            }
          }
        }
      }
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  } catch (e) {
    // Fallback é o setInterval
  }
})();
