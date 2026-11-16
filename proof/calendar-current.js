(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.79886063c3b57151.js","sha256":"79886063c3b571512343906df38009288fd71311fa806592802f266e29a383df","count":2086,"publishedAt":"2026-11-16T06:41:45Z","state":"calendar-state.json","stateSha256":"58ead7c661ce3fc744928045449dcceda6199d1b2b9bfa10c12c89ebb7e59f9b","sourceState":"calendar-source-state.json","sourceStateSha256":"15b3cc1377947e46f591ddf50cb7d57933d19cd36495347104e0f3f45b81648d"});
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
