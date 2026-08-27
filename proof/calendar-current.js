(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.596047655fe67990.js","sha256":"596047655fe67990226629e572cda0414589b32ca7559e11a030ec82d82c981a","count":1850,"publishedAt":"2026-08-27T20:21:48Z","state":"calendar-state.json","stateSha256":"eb374ebf51d145f6d2305cd963613a89196a4e24b4f21e7ca215a3242b44e324"});
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
