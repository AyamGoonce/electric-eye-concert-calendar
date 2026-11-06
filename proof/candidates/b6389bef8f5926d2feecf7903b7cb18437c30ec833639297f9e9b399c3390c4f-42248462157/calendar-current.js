(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b6389bef8f5926d2.js","sha256":"b6389bef8f5926d2feecf7903b7cb18437c30ec833639297f9e9b399c3390c4f","count":2036,"publishedAt":"2026-11-06T16:04:10Z","state":"calendar-state.json","stateSha256":"cd2e6f4c7734eda053705dc9a369f31c2abaaf20dc76e8485508a6d655f2d83b","sourceState":"calendar-source-state.json","sourceStateSha256":"952d27cc13015d22c22bcb543c8cffd23a5cee0f9c6fa6ada99c377e841bb9bf"});
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
