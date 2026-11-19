(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.37ff5792aa721e82.js","sha256":"37ff5792aa721e82c1c9e30ec0ac9ce49f6d502c1a815a823301126bb24ece69","count":2159,"publishedAt":"2026-11-19T20:44:18Z","state":"calendar-state.json","stateSha256":"72f3e7e8506e9d7703f8f795ba5ba8eee9f539328e37d7151b31218ec2d7894d","sourceState":"calendar-source-state.json","sourceStateSha256":"0e4f1d206f31ac5450ff336917659c34b40355f17d69cf5a080aded06f1000b9"});
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
