(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.051b4fc66049a3e7.js","sha256":"051b4fc66049a3e7b48d1b7fad9e577c4a91cc7bd1acce6b06b77086d7afffe8","count":2101,"publishedAt":"2026-11-17T03:57:30Z","state":"calendar-state.json","stateSha256":"8d3681ee3cdd3f941f15e6a992235b2a3cdd8e8e6fd7e5692d5bc0980c7ba383","sourceState":"calendar-source-state.json","sourceStateSha256":"17c632f6d4c753da2924c0122494a72b703068336b6a181963ab2dd5301618b0"});
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
