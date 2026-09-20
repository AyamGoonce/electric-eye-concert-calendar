(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.aad6e3783a8ad610.js","sha256":"aad6e3783a8ad610125a58c4851dd1cb35147376b227c537fa0d88d9374cff9a","count":2172,"publishedAt":"2026-09-20T11:35:36Z","state":"calendar-state.json","stateSha256":"84b7231cd10f8f1112050627a5a142c8a7a695671fd306ccb752ec74daad4010"});
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
