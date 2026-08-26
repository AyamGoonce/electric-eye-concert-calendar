(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6558b358e8c42b3d.js","sha256":"6558b358e8c42b3d5168313a64e733a3c9b2b8dec9dd08f9ef5f3b978a89fbea","count":1712,"publishedAt":"2026-08-26T07:14:38Z","state":"calendar-state.json","stateSha256":"b25e4070590a6e141a7f6d99e824874185410ed84724eefe6d6f098aa0630603"});
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
