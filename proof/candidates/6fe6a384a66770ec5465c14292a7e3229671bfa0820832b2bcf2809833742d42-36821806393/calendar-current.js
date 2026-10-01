(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6fe6a384a66770ec.js","sha256":"6fe6a384a66770ec5465c14292a7e3229671bfa0820832b2bcf2809833742d42","count":2220,"publishedAt":"2026-10-01T05:52:10Z","state":"calendar-state.json","stateSha256":"a29e5f2fe9507608643ed54d51db94d84e98c984df0eb4e5bcd84ca752a50b3a","sourceState":"calendar-source-state.json","sourceStateSha256":"894c700975cd8734ebe45b425c0a05567cc775df3b8e056878973ea38f1e2f76"});
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
