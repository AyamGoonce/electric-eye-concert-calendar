(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.10df52444ad8d21e.js","sha256":"10df52444ad8d21e7a56f3bf284412113ae3ce2bb14c703d65af2bc1956eba4b","count":2214,"publishedAt":"2026-10-02T09:52:27Z","state":"calendar-state.json","stateSha256":"3b37b37947b1560d5e56d88beeab48f0e5f13700576ac5c40eb387e42e8df112","sourceState":"calendar-source-state.json","sourceStateSha256":"8df9a431431affa322d7e2d37c329aacd3157c74c503b84f2eb78eaa768c6086"});
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
