(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ca261067ee7bc318.js","sha256":"ca261067ee7bc318423892662a63c98a26cc74c1d34a2653992d0dab7647fdec","count":2151,"publishedAt":"2026-10-12T10:06:03Z","state":"calendar-state.json","stateSha256":"72ebe96c5689f1bdc02f1fa93637eda06cfbc1a8bef28130098b7c6bec017596","sourceState":"calendar-source-state.json","sourceStateSha256":"2ca7f84dfbbff7341778e5f37376f790dd998925cdb476729a3dd32b7ffd4f0c"});
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
