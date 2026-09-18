(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ea257aa42e04df13.js","sha256":"ea257aa42e04df13776a29e1648e85ffb76fb6e10dd7481dca717770a8c0bd1e","count":2209,"publishedAt":"2026-09-18T16:32:58Z","state":"calendar-state.json","stateSha256":"1e5f34e3228409fc5c313694a9b5d71a55d842aae44605b1578b72bcefbf2c73"});
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
