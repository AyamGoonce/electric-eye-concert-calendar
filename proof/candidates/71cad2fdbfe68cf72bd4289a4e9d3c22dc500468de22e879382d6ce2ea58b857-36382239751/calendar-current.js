(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.71cad2fdbfe68cf7.js","sha256":"71cad2fdbfe68cf72bd4289a4e9d3c22dc500468de22e879382d6ce2ea58b857","count":2061,"publishedAt":"2026-09-28T05:31:26Z","state":"calendar-state.json","stateSha256":"f3813e6c2da40b66a0c660113a6dccdd0b9c5407367a05f4692caa6921f72dce","sourceState":"calendar-source-state.json","sourceStateSha256":"6f9b82e5935901c04aae61533af06ee097354c6302aed5802f6a357a788c5d24"});
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
