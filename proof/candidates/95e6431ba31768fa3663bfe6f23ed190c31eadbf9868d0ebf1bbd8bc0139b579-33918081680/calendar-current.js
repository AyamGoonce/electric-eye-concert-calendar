(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.95e6431ba31768fa.js","sha256":"95e6431ba31768fa3663bfe6f23ed190c31eadbf9868d0ebf1bbd8bc0139b579","count":2535,"publishedAt":"2026-09-04T20:59:02Z","state":"calendar-state.json","stateSha256":"760d456cafdb3918a7052134cf73adea15dfd8c9ce6e5c6f67b5997aaf9275aa"});
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
