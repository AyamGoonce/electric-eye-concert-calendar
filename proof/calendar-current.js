(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.bdc2874758b7c857.js","sha256":"bdc2874758b7c8579470e742fff277b7c928e4cc7add3caf0c262b3a8fde2fc4","count":1980,"publishedAt":"2026-11-09T14:44:30Z","state":"calendar-state.json","stateSha256":"8562c4edf1f196835102157fde580c60766fc6431d1c5b0fd8f9bc4dc400746f","sourceState":"calendar-source-state.json","sourceStateSha256":"b6754bcb2f52c7dc4fea0852dc3658399dbbab8df3e64617819a70f8abf518fc"});
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
