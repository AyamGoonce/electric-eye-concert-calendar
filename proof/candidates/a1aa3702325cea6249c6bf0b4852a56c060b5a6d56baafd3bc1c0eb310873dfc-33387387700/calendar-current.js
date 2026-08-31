(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a1aa3702325cea62.js","sha256":"a1aa3702325cea6249c6bf0b4852a56c060b5a6d56baafd3bc1c0eb310873dfc","count":2057,"publishedAt":"2026-08-31T11:39:58Z","state":"calendar-state.json","stateSha256":"6bc1d0ed25fff1116719a4b7104c55723010e2ef1daa33e9bbb6bcf7969ee40a"});
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
