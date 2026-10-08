(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.91f0994e34de086a.js","sha256":"91f0994e34de086ace24d84c2952688c713639bb04a2d2e38a7da1cc0e52fcec","count":2215,"publishedAt":"2026-10-08T23:43:23Z","state":"calendar-state.json","stateSha256":"5623779f9db7b764e7bb28674d67e6452062ffc5fd3055ba96876aaacf654cbd","sourceState":"calendar-source-state.json","sourceStateSha256":"eb23fe6888f6ded2c18072166c20e351ad64e6fe94f28203711d2a35ae92b826"});
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
