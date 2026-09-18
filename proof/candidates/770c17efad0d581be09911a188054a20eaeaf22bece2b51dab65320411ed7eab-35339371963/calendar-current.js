(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.770c17efad0d581b.js","sha256":"770c17efad0d581be09911a188054a20eaeaf22bece2b51dab65320411ed7eab","count":2502,"publishedAt":"2026-09-18T11:27:26Z","state":"calendar-state.json","stateSha256":"d9dae1275e70a7ecc181fac3ab3970684e42b6cb5c7db9e588efd317b669af06"});
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
