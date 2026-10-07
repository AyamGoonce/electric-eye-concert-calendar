(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cc28219ee07889d3.js","sha256":"cc28219ee07889d327e76cb12ad0364ad23869dce2c2f161506e903dcac0c914","count":2195,"publishedAt":"2026-10-07T06:39:23Z","state":"calendar-state.json","stateSha256":"818a71bceb029089520aa1e11d06c308e18ac53880a53afc4ad2bb1d9d81b1e3","sourceState":"calendar-source-state.json","sourceStateSha256":"ba76a992cb4672556cfdc3dadc3ba65f8f7fb2fed5e812702599614dfa7e0b6d"});
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
