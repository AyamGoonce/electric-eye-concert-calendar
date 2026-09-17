(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.52fcea9bb56a3614.js","sha256":"52fcea9bb56a3614f85350d5531df22ea35f691eeb1e081d996f92facf42bac6","count":2522,"publishedAt":"2026-09-17T11:52:37Z","state":"calendar-state.json","stateSha256":"f93b0562629384646770aa56ce8722c5807524ab2c04a78496b2be36832e6ed9"});
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
