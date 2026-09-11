(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e307864444866781.js","sha256":"e30786444486678142714d6489522c185bf4863cb4991bbcb975c918579e7b3d","count":2256,"publishedAt":"2026-09-11T04:50:14Z","state":"calendar-state.json","stateSha256":"f51e21ada36bee3248286a6402b4bad10f509be5621831c91b179f5342546aba"});
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
