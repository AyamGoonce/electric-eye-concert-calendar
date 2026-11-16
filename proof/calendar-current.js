(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4cac813506704854.js","sha256":"4cac813506704854966f60383262679f64fdc46c6bba61ae8d4458ce491244a9","count":2114,"publishedAt":"2026-11-16T19:39:55Z","state":"calendar-state.json","stateSha256":"88a3113eb5253acf7a59369585146cbecfec760acd2ad49c8c02ea5ec0ff1595","sourceState":"calendar-source-state.json","sourceStateSha256":"21436954d044d4b2a6079739b8bbffa0068386d03354b65911f5518c302542e8"});
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
