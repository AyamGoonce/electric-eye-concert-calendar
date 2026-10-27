(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.57952941c9f91dde.js","sha256":"57952941c9f91dde2339b25a9b1eb07968170efa0be510736b4a29ce871ddfad","count":2043,"publishedAt":"2026-10-27T10:41:57Z","state":"calendar-state.json","stateSha256":"5b2c623b4012527c99043afe89436b093de0d2e49e320a717424c4b1b5fa7120","sourceState":"calendar-source-state.json","sourceStateSha256":"dd197908fb65e8fe396c7f46c7700a310960c5ed347ae071efb1d2ca24d6212e"});
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
