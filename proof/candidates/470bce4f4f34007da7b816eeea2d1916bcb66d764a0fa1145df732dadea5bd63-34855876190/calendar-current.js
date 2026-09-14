(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.470bce4f4f34007d.js","sha256":"470bce4f4f34007da7b816eeea2d1916bcb66d764a0fa1145df732dadea5bd63","count":2456,"publishedAt":"2026-09-14T14:33:21Z","state":"calendar-state.json","stateSha256":"40b293dfeb3cdd3a3d681a18b2c13cd5cb70b6f0e95ce1163614d640ecccd662"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
