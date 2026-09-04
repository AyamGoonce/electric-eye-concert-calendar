(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.86db76118c1985ee.js","sha256":"86db76118c1985ee2a18b03e8048efe0bdeff711ce41b3f723ef132c4d0b3a8b","count":2461,"publishedAt":"2026-09-04T23:15:23Z","state":"calendar-state.json","stateSha256":"385fb0fc3d7ae019c29881201b5744b460a75d922c1bbf4319e3c8ee403c8882"});
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
