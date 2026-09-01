(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.264312dc3fb41e57.js","sha256":"264312dc3fb41e577ea2ef1ceff3ce03de5111747143243943ff3f0336cbe293","count":2081,"publishedAt":"2026-09-01T05:21:00Z","state":"calendar-state.json","stateSha256":"b877a0b15994281d8f13f98b9717b1c281c8a8ec04589bbf5e4560d2da4ba232"});
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
