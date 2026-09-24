(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ae47c33744adf377.js","sha256":"ae47c33744adf377bf0d88825412b20c2fbd7fe1bce68f45b82538c8050fa736","count":2136,"publishedAt":"2026-09-24T10:30:58Z","state":"calendar-state.json","stateSha256":"18515c1131bffcd124f53814fccbbbd6d8d8bad3cb69f34f3690c2915de8e8ce","sourceState":"calendar-source-state.json","sourceStateSha256":"2cc078f79c5287a784f2ef9d4813cbde9e2bb66766c28cdc70b7ef1d98908304"});
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
