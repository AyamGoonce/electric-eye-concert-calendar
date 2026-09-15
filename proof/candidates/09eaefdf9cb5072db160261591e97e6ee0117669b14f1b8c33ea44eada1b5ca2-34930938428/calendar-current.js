(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.09eaefdf9cb5072d.js","sha256":"09eaefdf9cb5072db160261591e97e6ee0117669b14f1b8c33ea44eada1b5ca2","count":2454,"publishedAt":"2026-09-15T05:03:36Z","state":"calendar-state.json","stateSha256":"ac4c33f1fd9db87a0c88acc3bc5407418f0b2abf0310a0475c1f875473304194"});
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
