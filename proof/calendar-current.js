(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.74af84bd19d6bfbe.js","sha256":"74af84bd19d6bfbed13fcce7005690d2933ec6d43363933ca1e6bba6564c7d55","count":2485,"publishedAt":"2026-09-15T21:29:21Z","state":"calendar-state.json","stateSha256":"cc140b6274a10eb71debdbe83a537b9ac70525c58ccc4deccde31ea0196f9a48"});
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
