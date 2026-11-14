(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6760071f6ac95c77.js","sha256":"6760071f6ac95c774b4b6415e7c1aa62e29c669ea3720654cf82e5fc491f6ba7","count":2137,"publishedAt":"2026-11-14T22:31:48Z","state":"calendar-state.json","stateSha256":"afbc99c52a384d32e4e6f3b741b8e5bc054782dfcf5e310504d4309f15da2707","sourceState":"calendar-source-state.json","sourceStateSha256":"f7a3a5a662e17dda25d2037a8dbd3f9019736edcc9a7356065fc46e6d2175ace"});
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
