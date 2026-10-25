(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ad4c8c097ced241e.js","sha256":"ad4c8c097ced241ecc82a9fa3b885e4af92a4117c3b8b5be4ff65d12092baea8","count":2048,"publishedAt":"2026-10-25T11:43:04Z","state":"calendar-state.json","stateSha256":"e50cb789020202b2010a2c9c430db29ebd897416adddfae38b96eef8d24e4793","sourceState":"calendar-source-state.json","sourceStateSha256":"36cc74d88534c04aac5a4f23bdf07e4bba1c1f9acba12890fcf826f84450eb82"});
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
