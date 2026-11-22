(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3b5d763c2de6dfd0.js","sha256":"3b5d763c2de6dfd00ac1bd075b094db17d80e0f381865cbf78b8a8d42313e34d","count":2100,"publishedAt":"2026-11-22T01:23:48Z","state":"calendar-state.json","stateSha256":"ee2bebcee37aa16fa8175b5f9ee0f633eb482232d66d6a91e72e7b225c7bcbc0","sourceState":"calendar-source-state.json","sourceStateSha256":"e3af7b1025b18a9366becebac261138fbcfeee3ef378e17b7fea518de8886652"});
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
