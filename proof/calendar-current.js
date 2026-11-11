(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e306030cd7fdc5f8.js","sha256":"e306030cd7fdc5f8863f6f86aae4823ca4994c0cdcad4cb5953cf25101e8fb1b","count":2158,"publishedAt":"2026-11-11T18:41:56Z","state":"calendar-state.json","stateSha256":"eff81d60d6617edc06ef9f929d737bc7fa5cadd829af2a2313d2014d62e69677","sourceState":"calendar-source-state.json","sourceStateSha256":"0b32db2b37602f24d1ca44c9d274b0b1f1f549fe4a6c544384a6cadf3729c8f9"});
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
