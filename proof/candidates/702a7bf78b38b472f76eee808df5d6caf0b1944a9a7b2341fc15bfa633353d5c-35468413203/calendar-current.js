(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.702a7bf78b38b472.js","sha256":"702a7bf78b38b472f76eee808df5d6caf0b1944a9a7b2341fc15bfa633353d5c","count":2193,"publishedAt":"2026-09-19T20:49:56Z","state":"calendar-state.json","stateSha256":"8a297750c051ccf9f6fcda3b3dbabd1b5118379bf087dae4be23cca79a082d5f"});
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
