(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ce4f98338d7da9f7.js","sha256":"ce4f98338d7da9f7ff72693bf8b5d0b31cea607be41d526d147bfd246cd25150","count":2079,"publishedAt":"2026-10-24T00:36:57Z","state":"calendar-state.json","stateSha256":"464638e098b73c5a22c51e37d14308ba758b49e35e8694e2e6e5fabc79278c8d","sourceState":"calendar-source-state.json","sourceStateSha256":"657e40cf4dc5a08358516fb893391aa247598e32be4fb808e1bbdede2f558169"});
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
