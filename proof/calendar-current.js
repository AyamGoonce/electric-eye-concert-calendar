(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6784742487bd1326.js","sha256":"6784742487bd1326320556bbcf8d524d19140d1634eb175fcdbf4bee72f739aa","count":1981,"publishedAt":"2026-11-08T17:59:58Z","state":"calendar-state.json","stateSha256":"b3cc138e1eec0768350e656fb1d092b0b58d3f34356b4ae81013db747da9e58b","sourceState":"calendar-source-state.json","sourceStateSha256":"a4b1f9f0d0df3dd316ffa9c62689bb9d57827690e7454ae9d6ba55eace1d2ce7"});
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
