(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.188d47cf41921131.js","sha256":"188d47cf419211311359662c3a3626a6e4dc05c1e18a1b9b6ba6e7f8d5477e43","count":1729,"publishedAt":"2026-08-24T07:37:02Z","state":"calendar-state.json","stateSha256":"1bd58591e4616ac6beab53c41b6a6b34534a40bd875020a7b3c9f3ec92eb501d"});
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
