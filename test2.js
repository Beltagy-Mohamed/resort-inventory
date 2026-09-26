
      // Show only on iOS Safari, and if NOT already in standalone mode
      const isIos = () => {
        const userAgent = window.navigator.userAgent.toLowerCase();
        return /iphone|ipad|ipod/.test( userAgent );
      }
      const isStandalone = () => ('standalone' in window.navigator) && (window.navigator.standalone);
      
      if (isIos() && !isStandalone()) {
          // Check if we haven't shown it recently (e.g. session storage)
          if (!sessionStorage.getItem('iosBannerDismissed')) {
              document.getElementById('ios-pwa-banner').style.display = 'block';
              document.getElementById('ios-pwa-banner').querySelector('button').addEventListener('click', function() {
                  sessionStorage.setItem('iosBannerDismissed', 'true');
              });
          }
      }
  
