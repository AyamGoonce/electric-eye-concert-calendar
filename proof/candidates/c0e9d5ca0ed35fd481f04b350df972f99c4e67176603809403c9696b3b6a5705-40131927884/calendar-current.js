(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c0e9d5ca0ed35fd4.js","sha256":"c0e9d5ca0ed35fd481f04b350df972f99c4e67176603809403c9696b3b6a5705","count":2072,"publishedAt":"2026-10-24T20:57:27Z","state":"calendar-state.json","stateSha256":"b06e9c6bab3da59cd9ae560dd3f1dc18769e243f00fe21ae578dc3180ce5b94e","sourceState":"calendar-source-state.json","sourceStateSha256":"a50e4db4e649b2897e6a9dbc073c75ca36fd4f81f69216847a2b522673c303c9"});
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
