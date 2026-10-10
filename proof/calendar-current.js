(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a918ac2780dfe868.js","sha256":"a918ac2780dfe8682ca4a93094ea9ceebcd7e21058eb9784976220b5aadbab6e","count":2194,"publishedAt":"2026-10-10T07:43:11Z","state":"calendar-state.json","stateSha256":"3ce6c65954d37c6ae9f8a30bc6eab35f2a00536579dce537482b166cbfa0530e","sourceState":"calendar-source-state.json","sourceStateSha256":"f6025e35c6f06630cfcc78d3bf3226d11fc648057a91b5ff35bb5d3da5a28f36"});
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
