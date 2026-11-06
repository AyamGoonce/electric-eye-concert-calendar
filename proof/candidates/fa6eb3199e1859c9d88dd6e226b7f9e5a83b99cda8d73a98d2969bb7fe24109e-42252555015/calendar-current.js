(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.fa6eb3199e1859c9.js","sha256":"fa6eb3199e1859c9d88dd6e226b7f9e5a83b99cda8d73a98d2969bb7fe24109e","count":2037,"publishedAt":"2026-11-06T16:30:23Z","state":"calendar-state.json","stateSha256":"1e3522b806c38f0e1baee5423c073a5c40d63eaf69ab912821ff1f95483928a8","sourceState":"calendar-source-state.json","sourceStateSha256":"4f65188a1b85a499a9daaacb11df2d1771477c6138bbd93b48f6c009190e122d"});
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
