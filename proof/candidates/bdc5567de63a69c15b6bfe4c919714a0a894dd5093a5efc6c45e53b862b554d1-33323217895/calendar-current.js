(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bdc5567de63a69c1.js","sha256":"bdc5567de63a69c15b6bfe4c919714a0a894dd5093a5efc6c45e53b862b554d1","count":2057,"publishedAt":"2026-08-30T16:50:06Z","state":"calendar-state.json","stateSha256":"75ed2cc9896093c65271ef262e6577b0806e063008b31e48ead04a457d3744d6"});
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
