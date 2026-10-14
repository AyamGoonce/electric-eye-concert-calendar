(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1f5e5e6dc0f05dbf.js","sha256":"1f5e5e6dc0f05dbfdcf681855501e6e7b10baf7c066abf1b0a23e04d1db9b0a4","count":2159,"publishedAt":"2026-10-14T12:03:31Z","state":"calendar-state.json","stateSha256":"82fab60ca8414743e696b851300b9c1fdfca5e074ce62fca9df6f2a7374a532f","sourceState":"calendar-source-state.json","sourceStateSha256":"3916864ed691310a1ad21427f5f0f009677e603a5c56a73b277babb6377948ec"});
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
