(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.8663c6a940bdd7ee.js","sha256":"8663c6a940bdd7ee02bc9ea1d58725ee540f70f5a7a20a5c9f0c358d4c30d19d","count":2209,"publishedAt":"2026-09-30T12:01:31Z","state":"calendar-state.json","stateSha256":"ac6e1e3c270e75114cb67c57040889580735e3f088980083392220691f081835","sourceState":"calendar-source-state.json","sourceStateSha256":"35cda02898befe5e0cb0389634a899fa839dd764d5ee5fc158aea23dc7ba1f2f"});
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
