(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.aab1650d8b55c6d5.js","sha256":"aab1650d8b55c6d5d0dbcb9fd87a99950722b95f694654f644bd5d8179c3026c","count":2071,"publishedAt":"2026-10-18T15:58:49Z","state":"calendar-state.json","stateSha256":"5e4b565f7f1f64cc9f3f95b47dc59f176240994697b3e2be683ba6ee81223ef5","sourceState":"calendar-source-state.json","sourceStateSha256":"c4f391b02fe97da45615f8a01807c305af727c1d4934cbbb394b615f0074fd4e"});
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
