(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.82480d0e9a2c3a6a.js","sha256":"82480d0e9a2c3a6a4670b3abd5621036d5cdf8b076160e6469a801656542f636","count":2038,"publishedAt":"2026-11-06T16:57:47Z","state":"calendar-state.json","stateSha256":"1598305fb00b0ee584ff7ceaceefcf3d1989728da0c8f371cc064ee1309e7a82","sourceState":"calendar-source-state.json","sourceStateSha256":"0fd4b2dbf50cd8e2bc2337ed02630f688c2b0130bc685510461e56ff8a1d3b99"});
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
