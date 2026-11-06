(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.543e56c79daee14c.js","sha256":"543e56c79daee14c4bcb6320606b1239f73736feb01020925e6603586d2f73ce","count":2035,"publishedAt":"2026-11-06T14:46:45Z","state":"calendar-state.json","stateSha256":"dad8e50a266dfb875b33f6b795665e672b9da305c32a46661c9bc068c2f3301d","sourceState":"calendar-source-state.json","sourceStateSha256":"705422e24bb753e4103617c48faf1ce458fda10d0e1bfce9ea32fc5f9d8c530b"});
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
