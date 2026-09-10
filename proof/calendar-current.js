(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.997d2d27e56f8977.js","sha256":"997d2d27e56f89777f90d01e61fce2a3b7c395d952402954774450d9003291b9","count":2486,"publishedAt":"2026-09-10T10:52:57Z","state":"calendar-state.json","stateSha256":"a9ed400772b765bf17ff5dc006d6da5092a3c2960a077ef25bcd76a59f9b9d63"});
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
